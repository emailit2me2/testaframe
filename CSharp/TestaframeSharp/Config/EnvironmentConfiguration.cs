using System;
using System.Collections.Generic;
using Testaframe.Utilities;

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
        public static string Hosts = "HOSTS";

        /// <summary>
        /// The allows writes key.
        /// </summary>
        public static string AllowsWrites = "ALLOWS_WRITES";
    }

    /// <summary>
    /// Spec key.
    /// </summary>
    public sealed class SpecKey
    {
        /// <summary>
        /// The host key.
        /// </summary>
        public static string Host = "Host";

        /// <summary>
        /// The port key.
        /// </summary>
        public static string Port = "Port";

        /// <summary>
        /// The URL template key.
        /// </summary>
        public static string UrlTemplate = "URL_TMPL";
    }

    /// <summary>
    /// Environment data class which is expected to be overwritten.
    /// </summary>
    public abstract class EnvironmentConfiguration
    {
        private Dictionary<string, MultiLevelDictionary> environments = new Dictionary<string, MultiLevelDictionary>();

        /// <summary>
        /// Gets the configuration for the environment.
        /// </summary>
        /// <value>The configuration dictionary.</value>
        public virtual Dictionary<string, MultiLevelDictionary> Environments
        {
            get
            {
                return this.environments;    
            }
        }
    }
}

