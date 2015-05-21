using System;
using System.Collections.Generic;

namespace Testaframe.Utilities
{
    /// <summary>
    /// String extensions.
    /// </summary>
    public static class StringExtensions
    {
        /// <summary>
        /// Format the specified string with named args.
        /// </summary>
        /// <param name="str">The format string.</param>
        /// <param name="args">The named args.</param>
        public static string Format(this String str, params KeyValuePair<string, string>[] args)
        {
            string formatted = str;
            foreach(var arg in args)
            {
                formatted = formatted.Replace("{" + arg.Key + "}", arg.Value);
            }
            return formatted;
        }

        /// <summary>
        /// Format the specified string with named args.
        /// </summary>
        /// <param name="str">The format string.</param>
        /// <param name="args">The named args.</param>
        /// <example>
        /// "{host}:{port}".Format(new Dictionary<string, string>() 
        ///                        {
        ///                            {"host", "http://127.0.0.1"}, 
        ///                            {"port", 80}
        ///                        }
        /// 
        /// Returns: "http://127.0.0.1:80"
        /// </example>
        public static string Format(this String str, Dictionary<string, string> args)
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

