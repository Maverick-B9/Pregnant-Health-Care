
import tensorflow as tf
import numpy as np
import os

model_path = 'app/model_path.h5'

if not os.path.exists(model_path):
    print(f"Model file not found at {model_path}")
    exit(1)


try:
    print("Loading model...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Model loaded.")
    
    scaler_path = 'app/scaler.pkl'
    if os.path.exists(scaler_path):
        import pickle
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f) 
        print("Scaler loaded.")
    else:
        print("Scaler not found!")
        exit(1)

    # Test Case 1: Low values (Healthy-ish)
    # pregn, glucose, bp, skin, insulin, bmi, dpf, age
    input1 = np.array([[0, 80, 60, 20, 0, 22.0, 0.2, 25]])
    input1_scaled = scaler.transform(input1)
    
    # Test Case 2: High values (Diabetic-ish)
    input2 = np.array([[5, 180, 90, 40, 200, 35.0, 1.2, 55]])
    input2_scaled = scaler.transform(input2)

    pred1 = model.predict(input1_scaled)
    pred2 = model.predict(input2_scaled)

    print(f"Prediction 1 (Low values): {pred1[0][0]}")
    print(f"Prediction 2 (High values): {pred2[0][0]}")

    if pred1[0][0] == pred2[0][0]:
        print("ALERT: Model returns IDENTICAL values for different inputs.")
    else:
        print("SUCCESS: Model returns different values.")

except Exception as e:
    print(f"Error: {e}")
