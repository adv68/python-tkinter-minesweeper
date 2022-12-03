using Microsoft.ML;
using Microsoft.ML.AutoML;
using Microsoft.ML.Data;
using MinesweeperML.NET;
using NumSharp.Extensions;
using static Microsoft.ML.DataOperationsCatalog;
using static TorchSharp.torch.utils;

//var trainedModel = mlContext.Model.Load(Path.GetFullPath("MLModel1.zip"), out DataViewSchema modelSchema);

//using (var stream = File.Create("sample_onnx_conversion_1.onnx"))
//    mlContext.Model.ConvertToOnnx(trainedModel, modelSchema, stream);


/*

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

*/


var mlContext = new MLContext();

var dataPath = Path.GetFullPath(@"..\..\..\..\..\..\trainingdata-2.csv");

var dataView = mlContext.Data.LoadFromTextFile<MinesweeperInput>(dataPath, hasHeader: true, separatorChar: ',');

TrainTestData trainValidationData = mlContext.Data.TrainTestSplit(dataView, testFraction: 0.2);


var pipeline = mlContext.Transforms.Conversion.MapValueToKey(inputColumnName: "Out", outputColumnName: "Label")
        .Append(mlContext.Transforms.Conversion.ConvertType(new[]
        {
            new InputOutputColumnPair("In00s", "In00"),
            new InputOutputColumnPair("In10s", "In10"),
            new InputOutputColumnPair("In20s", "In20"),
            new InputOutputColumnPair("In30s", "In30"),
            new InputOutputColumnPair("In40s", "In40"),
            new InputOutputColumnPair("In01s", "In01"),
            new InputOutputColumnPair("In11s", "In11"),
            new InputOutputColumnPair("In21s", "In21"),
            new InputOutputColumnPair("In31s", "In31"),
            new InputOutputColumnPair("In41s", "In41"),
            new InputOutputColumnPair("In02s", "In02"),
            new InputOutputColumnPair("In12s", "In12"),
            new InputOutputColumnPair("In22s", "In22"),
            new InputOutputColumnPair("In32s", "In32"),
            new InputOutputColumnPair("In42s", "In42"),
            new InputOutputColumnPair("In03s", "In03"),
            new InputOutputColumnPair("In13s", "In13"),
            new InputOutputColumnPair("In23s", "In23"),
            new InputOutputColumnPair("In33s", "In33"),
            new InputOutputColumnPair("In43s", "In43"),
            new InputOutputColumnPair("In04s", "In04"),
            new InputOutputColumnPair("In14s", "In14"),
            new InputOutputColumnPair("In24s", "In24"),
            new InputOutputColumnPair("In34s", "In34"),
            new InputOutputColumnPair("In44s", "In44")
        },
        DataKind.Single
        ))
        .Append(mlContext.Transforms.Concatenate("Features", new[] { "In00s", "In10s", "In20s", "In30s", "In40s", "In01s", "In11s", "In21s", "In31s", "In41s", "In02s", "In12s", "In22s", "In32s", "In42s", "In03s", "In13s", "In23s", "In33s", "In43s", "In04s", "In14s", "In24s", "In34s", "In44s" }))
        .AppendCacheCheckpoint(mlContext);

var trainingPipeline = pipeline.Append(mlContext.MulticlassClassification.Trainers.LightGbm("Label", "Features"))
        .Append(mlContext.Transforms.Conversion.MapKeyToValue("PredictedLabel"));

var trainedModel = trainingPipeline.Fit(trainValidationData.TrainSet);

var testMetrics = mlContext.MulticlassClassification.Evaluate(trainedModel.Transform(trainValidationData.TestSet));

Console.WriteLine($"*************************************************************************************************************");
Console.WriteLine($"*       Metrics for Multi-class Classification model - Test Data     ");
Console.WriteLine($"*------------------------------------------------------------------------------------------------------------");
Console.WriteLine($"*       MicroAccuracy:    {testMetrics.MicroAccuracy:0.###}");
Console.WriteLine($"*       MacroAccuracy:    {testMetrics.MacroAccuracy:0.###}");
Console.WriteLine($"*       LogLoss:          {testMetrics.LogLoss:#.###}");
Console.WriteLine($"*       LogLossReduction: {testMetrics.LogLossReduction:#.###}");
Console.WriteLine($"*************************************************************************************************************");

mlContext.Model.Save(trainedModel, trainValidationData.TrainSet.Schema, "LightGbmModel.zip");
