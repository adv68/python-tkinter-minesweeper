import pandas as pd
from tensorflow import keras
from keras import layers

if __name__ == "__main__":
    trainingdata = pd.read_csv("trainingdata.csv")
    trainingdata.head()

    td_in = trainingdata.iloc[:, 0 : 25].values
    td_out = trainingdata.iloc[:, 25 : 27].values

    model = keras.Sequential()
    model.add(layers.Dense(32, input_dim=25, activation="linear"))
    model.add(layers.Dense(32, activation="linear"))
    model.add(layers.Dense(2, activation="linear"))

    model.compile(optimizer="adam", loss="mae")

    losses = model.fit(
        x=td_in, 
        y=td_out,
        epochs=10,
        validation_split=0.1
    )

    model.save("keras_model")

    loss_dataframe = pd.DataFrame(losses.history)
    loss_dataframe.loc[:,["loss", "val_loss"]].plot()


    
    