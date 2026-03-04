"""
Project: IoT Device
Auto-generated
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras import layers

class IoTDeviceModel:
    """A class to represent an IoT device model for predicting sensor data."""

    def __init__(self):
        """Initialize the IoT device model with a simple neural network architecture."""
        self.model = self.build_model()

    def build_model(self):
        """Build and compile the neural network model."""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(10,)),  # Input layer with 10 features
            layers.Dense(32, activation='relu'),  # Hidden layer
            layers.Dense(1)  # Output layer for regression
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')  # Compile the model
        return model

    def train(self, X, y, epochs=100, batch_size=32):
        """Train the model on the provided data.

        Args:
            X (np.ndarray): Input features.
            y (np.ndarray): Target values.
            epochs (int): Number of training epochs.
            batch_size (int): Size of training batches.
        """
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)  # Fit the model

    def predict(self, X):
        """Make predictions using the trained model.

        Args:
            X (np.ndarray): Input features for prediction.

        Returns:
            np.ndarray: Predicted values.
        """
        return self.model.predict(X)  # Return predictions

def generate_synthetic_data(num_samples=1000):
    """Generate synthetic sensor data for training and testing.

    Args:
        num_samples (int): Number of samples to generate.

    Returns:
        tuple: Features and target values as numpy arrays.
    """
    np.random.seed(42)  # For reproducibility
    X = np.random.rand(num_samples, 10)  # Generate random features
    y = np.sum(X, axis=1) + np.random.normal(0, 0.1, num_samples)  # Target is the sum of features with noise
    return X, y

def main():
    """Main function to execute the IoT device model training and prediction."""
    # Generate synthetic data
    X, y = generate_synthetic_data()

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)  # Fit and transform training data
    X_test = scaler.transform(X_test)  # Transform testing data

    # Create and train the IoT device model
    iot_model = IoTDeviceModel()
    iot_model.train(X_train, y_train, epochs=50, batch_size=16)

    # Make predictions on the test set
    predictions = iot_model.predict(X_test)

    # Plot the results
    plt.scatter(y_test, predictions)
    plt.xlabel('True Values')
    plt.ylabel('Predictions')
    plt.title('True vs Predicted Values')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red')  # Diagonal line
    plt.show()

if __name__ == "__main__":
    main()