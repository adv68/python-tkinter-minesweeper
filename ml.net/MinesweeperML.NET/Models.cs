using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.ML.Data;

namespace MinesweeperML.NET
{
    public class MinesweeperInput
    {
        [LoadColumn(0)]
        public int In00 { get; set; }
        [LoadColumn(1)]
        public int In10 { get; set; }
        [LoadColumn(2)]
        public int In20 { get; set; }
        [LoadColumn(3)]
        public int In30 { get; set; }
        [LoadColumn(4)]
        public int In40 { get; set; }
        [LoadColumn(5)]
        public int In01 { get; set; }
        [LoadColumn(6)]
        public int In11 { get; set; }
        [LoadColumn(7)]
        public int In21 { get; set; }
        [LoadColumn(8)]
        public int In31 { get; set; }
        [LoadColumn(9)]
        public int In41 { get; set; }
        [LoadColumn(10)]
        public int In02 { get; set; }
        [LoadColumn(11)]
        public int In12 { get; set; }
        [LoadColumn(12)]
        public int In22 { get; set; }
        [LoadColumn(13)]
        public int In32 { get; set; }
        [LoadColumn(14)]
        public int In42 { get; set; }
        [LoadColumn(15)]
        public int In03 { get; set; }
        [LoadColumn(16)]
        public int In13 { get; set; }
        [LoadColumn(17)]
        public int In23 { get; set; }
        [LoadColumn(18)]
        public int In33 { get; set; }
        [LoadColumn(19)]
        public int In43 { get; set; }
        [LoadColumn(20)]
        public int In04 { get; set; }
        [LoadColumn(21)]
        public int In14 { get; set; }
        [LoadColumn(22)]
        public int In24 { get; set; }
        [LoadColumn(23)]
        public int In34 { get; set; }
        [LoadColumn(24)]
        public int In44 { get; set; }
        [LoadColumn(25)]
        public int Out { get; set; }
    }

    public class MinesweeperOutput
    {
        [ColumnName("Prediction")]
        public int Out { set; get; }
    }
}
