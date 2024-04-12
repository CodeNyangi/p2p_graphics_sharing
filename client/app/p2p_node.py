import grpc
from concurrent import futures
import tasks_pb2_grpc
import tasks_pb2  # Assuming this protobuf file defines the necessary request and response messages
from utils import rent_gpu, start_training_session, complete_training_session
import threading
import train_finetune
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
    
      # New RPC methods based on updated tasks.proto
    def StartTrainingSession(self, request, context):
        dataset_path = './received_data'
        os.makedirs(dataset_path, exist_ok=True)
        with open(os.path.join(dataset_path, 'dataset.zip'), 'wb') as f:
            f.write(request.model_data)
        # Assume dataset is a zip file, extract, and prepare data
        gpu_id = request.gpu_id
        model_data = request.model_data

        # Deserialize the model data
        model = model_data.model
        dataset = model_data.dataset
        parameters = model_data.parameters

        # Make Parameter Hash by model_data
        parameter_hash = hash(model_data)
        session_id = start_training_session(gpu_id, parameter_hash)
        train_finetune.fine_tune_model(model, dataset, parameters)

        # When done training, complete the training session
        complete_training_session(session_id, is_completed=True)

        return tasks_pb2.SessionResponse(session_id=session_id)

    def UpdateModelParameters(self, request, context):
        model_parameters = request.model_parameters
        self.update_local_model(model_parameters)
        return tasks_pb2.UpdateModelParametersResponse(status="updated")

    def update_local_model(self, parameters):
        # Implement this method to update model parameters
        pass

if __name__ == "__main__":
    node = P2PNode()
    node.start_server()
