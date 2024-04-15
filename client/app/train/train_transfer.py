# train_transfer.py
import tensorflow as tf
import pickle
from p2p_node import send_model_parameters

def transfer_model(self, model, dataset_path, hyperparameters, strategy_type):
    # Load dataset
    train_dataset = tf.data.experimental.load(dataset_path)

    # Modify the model for transfer learning
    base_model = model
    base_model.trainable = False  # Freeze the base layers

    # Add new trainable layers on top
    global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
    prediction_layer = tf.keras.layers.Dense(1)
    model = tf.keras.Sequential([
        base_model,
        global_average_layer,
        prediction_layer
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss='binary_crossentropy',
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
    
