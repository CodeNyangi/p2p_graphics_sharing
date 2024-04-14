# train_transfer.py
import tensorflow as tf

def transfer_model(model, dataset_path, hyperparameters):
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

    # Extract specific hyperparameters
    epochs = hyperparameters.epoch

    # Start training
    history = model.fit(train_dataset, epochs=epochs)

    return history
