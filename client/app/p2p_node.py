import grpc
from concurrent import futures
from gui import get_ring_reduce_target
import tasks_pb2_grpc
import tasks_pb2  # Assuming this protobuf file defines the necessary request and response messages
from utils import complete_training_session
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
        self.session_id = ''
        self.aggregator_address = ''
        tasks_pb2_grpc.add_TaskServiceServicer_to_server(self, self.server)

    def start_server(self):
        self.server.add_insecure_port(f"{self.host}:{self.port}")
        self.server.start()
        print(f"Server started on {self.host}:{self.port}.")
        self.server.wait_for_termination()

    def RentGPU(self, request, context):
        """gRPC method to rent a GPU and start a training session."""
        self.aggregator_address = request.aggregator_address
        return tasks_pb2.GenericResponse(status ="success")
    
    def StartTrainingSession(self, request, context):
        dataset_path = './received_data'
        os.makedirs(dataset_path, exist_ok=True)
        self.session_id = request.session_id

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
            return tasks_pb2.SessionResponse(session_id=self.session_id)

        # Assume the dataset is sent as a path to a zip file that needs extraction
        try:
            with ZipFile(dataset, 'r') as zip_ref:
                zip_ref.extractall(dataset_path)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to extract dataset: {str(e)}')
            return tasks_pb2.SessionResponse(session_id=self.session_id)
        
        try:
            if training_type == 'fine_tune':
                train_finetune.fine_tune_model(model, dataset_path, hyperparameters) 
            else:
                train_transfer.transfer_model(model, dataset_path, hyperparameters)
            complete_training_session(self.session_id, is_completed=True)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Training failed: ' + str(e))
            return tasks_pb2.SessionResponse(session_id=self.session_id)

        return tasks_pb2.SessionResponse(session_id=self.session_id)
    
    def ReduceModelParameters(self, request, context):
        """gRPC method to receive model parameters from the aggregator."""
        session_id = request.session_id
        parameters = request.parameters

        if session_id != self.session_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Session ID mismatch.')
            return tasks_pb2.GenericResponse(status="failed")

        # Update the model parameters
        self.update_model_parameters(session_id, parameters)

        return tasks_pb2.GenericResponse(status="received")
    
    # Aggregator methods
    def UpdateModelParameters(self, request, context):
        session_id = request.session_id
        parameters = request.parameters

        # ring all-reduce
        target_session_info = get_ring_reduce_target(session_id)
        stub = tasks_pb2_grpc.TaskServiceStub(target_session_info.address)
        response = stub.RentGPU(tasks_pb2.ReduceModelParametersRequest(session_id=target_session_info.session_id, parameters=parameters))

        if response.status == 'received':
            return tasks_pb2.GenericResponse(status="updated")
        else :
            return tasks_pb2.GenericResponse(status="failed")

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


    def update_model_parameters(session_id, parameters):
        # Update the model gradients
        pass


if __name__ == "__main__":
    node = P2PNode()
    node.start_server()
