using System;
using System.Collections.Generic;

namespace Testaframe.Utilities
{
    public static class StringExtensions
    {
        public static string FormatEx(this String str, params KeyValuePair<string, string>[] args)
        {
            string formatted = str;
            foreach(var arg in args)
            {
                formatted = formatted.Replace("{" + arg.Key + "}", arg.Value);
            }
            return formatted;
        }
    }
}

