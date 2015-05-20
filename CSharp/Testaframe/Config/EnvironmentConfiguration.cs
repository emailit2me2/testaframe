using System;
using System.Collections.Generic;
using Testaframe.Utilities;
using System.Dynamic;
using System.IO;

namespace Testaframe.Config
{
    /// <summary>
    /// System environment Enumeration.
    /// </summary>
    public enum SystemEnvironment
    {
        /// <summary>
        /// LocalHost Environment.
        /// </summary>
        Localhost,

        /// <summary>
        /// Local Virtual Machine Environment.
        /// </summary>
        LocalVM,

        /// <summary>
        /// Development Environment.
        /// </summary>
        Dev,

        /// <summary>
        /// CI Environment.
        /// </summary>
        CI,

        /// <summary>
        /// Quality Assurance Environment.
        /// </summary>
        QA,

        /// <summary>
        /// Staging Environment.
        /// </summary>
        Staging,

        /// <summary>
        /// Production Environment.
        /// </summary>
        Prod
    }

    /// <summary>
    /// Spec group.
    /// </summary>
    public sealed class SpecGroup
    {
        /// <summary>
        /// The hosts key.
        /// </summary>
        public static readonly string Hosts = "HOSTS";

        /// <summary>
        /// The allows writes key.
        /// </summary>
        public static readonly string AllowsWrites = "ALLOWS_WRITES";
    }

    /// <summary>
    /// Spec key.
    /// </summary>
    public sealed class SpecKey
    {
        /// <summary>
        /// The host key.
        /// </summary>
        public static readonly string Host = "Host";

        /// <summary>
        /// The port key.
        /// </summary>
        public static readonly string Port = "Port";

        /// <summary>
        /// The URL template key.
        /// </summary>
        public static readonly string UrlTemplate = "URL_TMPL";
    }
        
    /// <summary>
    /// Static environment data 
    /// </summary>
    public static class EnvironmentConfiguration
    {
        private static MultiLevelDictionary environments;

        //TODO: Load in my_cfg and (our_envs) environment stuff as an JSON
        private static MultiLevelDictionary config;

        /// <summary>
        /// Gets the System environment configuration.
        /// </summary>
        /// <value>The configuration dictionary.</value>
        public static MultiLevelDictionary Environments
        {
            get
            {
                return environments;    
            }
        }

        /// <summary>
        /// Gets the configuration for the environment.
        /// </summary>
        /// <value>The configuration dictionary.</value>
        public static MultiLevelDictionary Config
        {
            get
            {
                return config;    
            }
        }

        /// <summary>
        /// Loads the environment from a JSON file.
        /// </summary>
        /// <param name="jsonFilename">JSON filename.</param>
        public static void LoadEnvironmentFromFile(string jsonFilename)
        {
            LoadEnvironment(ReadJsonFile(jsonFilename));  
        }

        /// <summary>
        /// Loads the config from a JSON file.
        /// </summary>
        /// <param name="jsonFilename">JSON filename.</param>
        public static void LoadConfigFromFile(string jsonFilename)
        {
            LoadConfig(ReadJsonFile(jsonFilename));  
        }

        /// <summary>
        /// Loads the environment from a JSON string.
        /// </summary>
        /// <param name="json">JSON string</param>
        public static void LoadEnvironment(string json)
        {
            environments = new MultiLevelDictionary(json);
        }

        /// <summary>
        /// Loads the config from a JSON string.
        /// </summary>
        /// <param name="json">JSON string</param>
        public static void LoadConfig(string json)
        {
            config = new MultiLevelDictionary(json);
        }

        /// <summary>
        /// Reads the json file.
        /// </summary>
        /// <returns>The json file.</returns>
        /// <param name="filename">Filename.</param>
        private static string ReadJsonFile(string filename)
        {
            string json = null;
            using (var reader = new StreamReader(filename))
            {
                json = reader.ReadToEnd();
            }
            return json;
        }
    }
}

