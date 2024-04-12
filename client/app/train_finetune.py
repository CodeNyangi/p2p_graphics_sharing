import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from transformers import AutoModel, AutoTokenizer
from huggingface_hub import hf_hub_url
import grpc
import tasks_pb2_grpc
import tasks_pb2

# get model from huggingface
def setup_model(model_name):
    model = AutoModel.from_pretrained(model_name)
    return model

def fine_tune_model( model, datasets, parameters):
    device = parameters.device
    epochs = parameters.epochs
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for images, labels in datasets:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}, Average Loss: {total_loss / len(datasets)}")
        
        # TODO 
        # update parameter call grpc function UpdateModelParameters
        channel = grpc.insecure_channel('localhost:50051')
        stub = tasks_pb2_grpc.TaskServiceStub(channel)
        response = stub.UpdateModelParameters(tasks_pb2.UpdateModelParametersRequest(model_parameters=tasks_pb2.ModelParameters(epoch=epoch, device=device)))
        status = response.status
        print(f"Model parameters updated. Status: {status}.")

        
