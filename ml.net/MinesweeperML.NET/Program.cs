using Microsoft.ML;
using Microsoft.ML.AutoML;
using Microsoft.ML.Data;
using NumSharp.Extensions;
using static Microsoft.ML.DataOperationsCatalog;

//var trainedModel = mlContext.Model.Load(Path.GetFullPath("MLModel1.zip"), out DataViewSchema modelSchema);

//using (var stream = File.Create("sample_onnx_conversion_1.onnx"))
//    mlContext.Model.ConvertToOnnx(trainedModel, modelSchema, stream);


var mlContext = new MLContext();

var dataPath = Path.GetFullPath(@"..\..\..\..\..\..\trainingdata-2.csv");

ColumnInferenceResults columnInference =
    mlContext.Auto().InferColumns(dataPath, labelColumnName: "out", groupColumns: false);

TextLoader loader = mlContext.Data.CreateTextLoader(columnInference.TextLoaderOptions);

IDataView data = loader.Load(dataPath);

TrainTestData trainValidationData = mlContext.Data.TrainTestSplit(data, testFraction: 0.2);

SweepablePipeline pipeline =
    mlContext.Auto().Featurizer(data, columnInformation: columnInference.ColumnInformation)
        .Append(mlContext.Auto().Regression(labelColumnName: columnInference.ColumnInformation.LabelColumnName));

AutoMLExperiment experiment = mlContext.Auto().CreateExperiment();

experiment
    .SetPipeline(pipeline)
    .SetRegressionMetric(RegressionMetric.RSquared, labelColumn: columnInference.ColumnInformation.LabelColumnName)
    .SetTrainingTimeInSeconds(180)
    .SetDataset(trainValidationData);

mlContext.Log += (_, e) => {
    if (e.Source.Equals("AutoMLExperiment"))
    {
        Console.WriteLine(e.RawMessage);
    }
};

TrialResult experimentResults = await experiment.RunAsync();


mlContext.Model.Save(experimentResults.Model, data.Schema, "model.zip");

using (var stream = File.Create("modelonnx.onnx"))
    mlContext.Model.ConvertToOnnx(experimentResults.Model, data, stream);







