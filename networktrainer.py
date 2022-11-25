import pandas as pd
from tensorflow import keras
from keras import layers, initializers

if __name__ == "__main__":
    trainingdata = pd.read_csv("trainingdata.csv")
    trainingdata.head()

    td_in = trainingdata.iloc[:, 0 : 25].values
    td_out = trainingdata.iloc[:, 25 : 27].values

    # attempt 1 - 10 epochs
    # result: failure
    #model = keras.Sequential()
    #model.add(layers.Dense(32, input_dim=25, activation="linear"))
    #model.add(layers.Dense(32, activation="linear"))
    #model.add(layers.Dense(2, activation="linear"))

    # attempt 2 - 10 epochs
    # result: failure
    #model = keras.Sequential()
    #model.add(layers.Dense(32, input_dim=25, activation="linear"))
    #model.add(layers.Dense(32, activation="relu"))
    #model.add(layers.Dense(32, activation="relu"))
    #model.add(layers.Dense(2, activation="linear"))

    # attempt 3 - 10 epochs
    # result: failure
    #model = keras.Sequential()
    #model.add(layers.Dense(32, input_dim=25, activation="linear"))
    #model.add(layers.Dense(32, kernel_initializer=initializers.Ones(), activation="relu"))
    #model.add(layers.Dense(32, kernel_initializer=initializers.Ones(), activation="relu"))
    #model.add(layers.Dense(2, activation="linear"))

    # attempt 4 - 30 epochs
    # result: failure
    #model = keras.Sequential()
    #model.add(layers.Dense(32, input_dim=25, activation="linear"))
    #model.add(layers.Dense(32, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="sigmoid"))
    #model.add(layers.Dense(32, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="sigmoid"))
    #model.add(layers.Dense(2, activation="sigmoid"))

    # attempt 5 - 30 epochs
    # result: failure
    model = keras.Sequential()
    model.add(layers.Dense(32, input_dim=25, activation="linear"))
    model.add(layers.Dense(256, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="relu"))
    model.add(layers.Dense(512, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="tanh"))
    model.add(layers.Dense(256, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="sigmoid"))
    model.add(layers.Dense(32, kernel_initializer=initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None), activation="relu"))
    model.add(layers.Dense(2, activation="sigmoid"))

    # attempt 6 - 30 epochs
    # result:
    #model = keras.Sequential()
    #model.add(layers.Dense(64, input_dim=25))
    #model.add(layers.Dense(64))
    #model.add(layers.Dense(64))
    #model.add(layers.Dense(64))
    #model.add(layers.Dense(64))
    #model.add(layers.Dense(2, activation="sigmoid"))


    model.compile(optimizer="adam", loss="mae", metrics=["accuracy"])

    losses = model.fit(
        x=td_in, 
        y=td_out,
        epochs=500,
        validation_split=0.1
    )

    # attempt 1
    #model.save("keras_model")
    # attempt 2
    #model.save("keras_model2")
    # attempt 3
    #model.save("keras_model3")
    # attempt 4
    #model.save("keras_model4")
    # attempt 5
    model.save("keras_model5")
    # attempt 6
    #model.save("keras_model6")

    print(losses.history["accuracy"])

    model.summary()

    loss_dataframe = pd.DataFrame(losses.history)
    loss_dataframe.loc[:,["loss", "val_loss"]].plot()


    
    