# train_finetune.py
import tensorflow as tf
import pickle
from p2p_node import send_model_parameters

def fine_tune_model(self, model, dataset_path, hyperparameters, strategy_type):
    # Load dataset
    train_dataset = tf.data.experimental.load(dataset_path)

    # Configure the model for fine-tuning
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # Lower learning rate for fine-tuning
        loss='sparse_categorical_crossentropy',  # Example loss function
        metrics=['accuracy']
    )

    if strategy_type == 'Mirrored':
        strategy = tf.distribute.MirroredStrategy()
        with strategy.scope():
            model.fit(train_dataset, epochs=hyperparameters.epoch)
            self.send_current_weights()
    else:
        model.fit(train_dataset, epochs=hyperparameters.epoch)
        
def send_current_weights(self):
    # Serialize the model config and weights
    serialized_model = pickle.dumps((self.model.get_config(), self.model.get_weights()))
    # Send the model to the aggregator
    send_model_parameters(serialized_model)
    
