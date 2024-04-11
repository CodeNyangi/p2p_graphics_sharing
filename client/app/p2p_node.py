import grpc
from concurrent import futures
import tasks_pb2_grpc
import tasks_pb2  # Assuming this protobuf file defines the necessary request and response messages
from utils import rent_gpu, start_training_session, update_training, change_aggregator, release_gpu, adjust_platform_commission, update_gpu_compute_price

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

    def RentAndStartSession(self, request, context):
        """gRPC method to rent a GPU and start a training session."""
        response = rent_gpu(request.gpu_id, request.compute_units, request.model, request.dataset)
        session_id = start_training_session(request.gpu_id)
        print(f"Session {session_id} started for GPU {request.gpu_id}.")
        return tasks_pb2.SessionResponse(session_id=session_id)

    def UpdateTraining(self, request, context):
        """gRPC method to update training progress."""
        update_training(request.session_id, request.epoch, request.parameter_hash)
        print(f"Updating session {request.session_id} to epoch {request.epoch} with hash {request.parameter_hash}.")
        return tasks_pb2.GenericResponse(status="Training updated successfully.")

    def ChangeAggregator(self, request, context):
        """gRPC method to change the aggregator for a training session."""
        change_aggregator(request.session_id, request.new_aggregator)
        print(f"Changing aggregator for session {request.session_id} to {request.new_aggregator}.")
        return tasks_pb2.GenericResponse(status="Aggregator changed successfully.")

    def ReleaseGPU(self, request, context):
        """gRPC method to release a rented GPU."""
        release_gpu(request.gpu_id)
        print(f"GPU {request.gpu_id} released.")
        return tasks_pb2.GenericResponse(status="GPU released successfully.")

if __name__ == "__main__":
    node = P2PNode()
    node.start_server()
