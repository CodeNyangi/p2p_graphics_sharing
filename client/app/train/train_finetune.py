# train_finetune.py
import tensorflow as tf

def fine_tune_model(model, dataset_path, hyperparameters):
    # Load dataset
    train_dataset = tf.data.experimental.load(dataset_path)

    # Configure the model for fine-tuning
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # Lower learning rate for fine-tuning
        loss='sparse_categorical_crossentropy',  # Example loss function
        metrics=['accuracy']
    )

    # Extract specific hyperparameters
    epochs = hyperparameters.epoch

    # Start training
    history = model.fit(train_dataset, epochs=epochs)

    return history
