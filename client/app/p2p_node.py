import grpc
from concurrent import futures
import tasks_pb2_grpc
import tasks_pb2  # Assuming this protobuf file defines the necessary request and response messages
from utils import rent_gpu, start_training_session, complete_training_session
import pickle
import tensorflow as tf
from zipfile import ZipFile
import train_finetune
import train_transfer
import os

class P2PNode(tasks_pb2_grpc.TaskServiceServicer):
    def __init__(self, host='localhost', port=50051):
        self.host = host
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tasks_pb2_grpc.add_TaskServiceServicer_to_server(self, self.server)

    def start_server(self):
        self.server.add_insecure_port(f"{self.host}:{self.port}")
        self.server.start()
        print(f"Server started on {self.host}:{self.port}.")
        self.server.wait_for_termination()

    def RentGPU(self, request, context):
        """gRPC method to rent a GPU and start a training session."""
        response = rent_gpu(request.gpu_id, request.compute_units, request.value)
        print(f"Started for GPU {request.gpu_id}.")
        return tasks_pb2.GenericResponse(status ="success")
    
    def StartTrainingSession(self, request, context):
        dataset_path = './received_data'
        os.makedirs(dataset_path, exist_ok=True)

        try:
            # Deserialize the model and data
            model = self.deserialize_model(request.model_data)
            dataset = self.deserialize_data(request.dataset)  # Assuming this returns the path to the dataset file
            hyperparameters = request.hyperparameters  # Now holds the extra params

            # Accessing hyperparameters
            training_type = hyperparameters.training
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to deserialize data: {str(e)}')
            return tasks_pb2.SessionResponse(session_id='')

        # Assume the dataset is sent as a path to a zip file that needs extraction
        try:
            with ZipFile(dataset, 'r') as zip_ref:
                zip_ref.extractall(dataset_path)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to extract dataset: {str(e)}')
            return tasks_pb2.SessionResponse(session_id='')

        gpu_id = request.gpu_id
        params_hash = hash(request.hyperparameters)
        try:
            session_id = start_training_session(gpu_id, params_hash)
            if training_type == 'fine_tune':
                train_finetune.fine_tune_model(model, dataset_path, hyperparameters) 
            else:
                train_transfer.transfer_model(model, dataset_path, hyperparameters)
            complete_training_session(session_id, is_completed=True)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Training failed: ' + str(e))
            return tasks_pb2.SessionResponse(session_id='')

        return tasks_pb2.SessionResponse(session_id=session_id)

    def UpdateModelParameters(self, request, context):
        model_parameters = request.model_parameters
        self.update_local_model(model_parameters)
        return tasks_pb2.UpdateModelParametersResponse(status="updated")
    
    def update_local_model(self, parameters):
        # Implement this method to update model parameters
        pass

    def deserialize_model(serialized_model):
        # Deserialize the model config and weights
        model_config, model_weights = pickle.loads(serialized_model)
        # Reconstruct the model from config and set weights
        reconstructed_model = tf.keras.Model.from_config(model_config)
        reconstructed_model.set_weights(model_weights)
        return reconstructed_model

    def deserialize_data(serialized_data):
        # Deserialize data
        data = pickle.loads(serialized_data)
        return data

if __name__ == "__main__":
    node = P2PNode()
    node.start_server()
