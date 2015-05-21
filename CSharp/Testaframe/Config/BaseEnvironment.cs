using System;
using Testaframe.Page;
using Testaframe.Data;
using Testaframe.Utilities;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace Testaframe.Config
{
    /// <summary>
    /// Base System Environment
    /// </summary>
    public abstract class BaseEnvironment
    {
        /// <summary>
        /// The Environment name
        /// </summary>
        protected readonly SystemEnvironment name = SystemEnvironment.None;

        /// <summary>
        /// The java script filename provided for execution by injection.
        /// </summary>
        protected readonly string javaScriptFilename = "";

        /// <summary>
        /// Gets the Executable JavaScript.
        /// </summary>
        public virtual string ExecutableJS
        {
            get
            {                
                string js = null;
                using (var reader = new StreamReader(this.javaScriptFilename))
                {
                    js = reader.ReadToEnd();
                }
                return js;
            }
        }

        /// <summary>
        /// Prepares the environment for service runs.
        /// </summary>
        public abstract void PrepareForService()
        {
            throw new NotImplementedException("Must be overidden.");
        }

        /// <summary>
        /// Performs the necessary teardown for service runs.
        /// </summary>
        public abstract void TeardownForService()
        {
            throw new NotImplementedException("Must be overidden.");
        }

        /// <summary>
        /// Creates the data builder for the run.
        /// </summary>
        /// <returns>The data builder.</returns>
        public abstract DataBuilder CreateDataBuilder()
        {
            throw new NotImplementedException("Must be overidden.");
        }

        /// <summary>
        /// Gets the host by name.
        /// </summary>
        /// <returns>The host.</returns>
        /// <param name="hostName">The name of the host.</param>
        public virtual string GetHost(string hostName)
        {
            string host = EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName][SpecKey.Host].Value;
            return host;
        }

        /// <summary>
        /// Gets the port by host name.
        /// </summary>
        /// <returns>The port for the host.</returns>
        /// <param name="hostName">The name of the host.</param>
        public virtual string GetPort(string hostName)
        {
            string port = EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName].Get(
                SpecKey.Port, string.Empty);
            return port;
        }

        /// <summary>
        /// Gets the URL of the host with port by name.
        /// </summary>
        /// <returns>The full host URL.</returns>
        /// <param name="hostName">The name of the host.</param>
        public virtual string GetUrl(string hostName)
        {
            string host = GetHost(hostName);
            string port = GetPort(hostName);
            return EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName][SpecKey.UrlTemplate].Value.Format(
                new Dictionary<string, string>() {
                {"host", host},
                {"port", port}
            });
        }

        /// <summary>
        /// Gets whether the environment allows writing.
        /// </summary>
        /// <returns><c>true</c>, if writes was allowed, <c>false</c> otherwise.</returns>
        public virtual bool AllowsWrites()
        {
            Debug.Assert(EnvironmentConfiguration.Environments[this.name].ContainsKey(SpecGroup.AllowsWrites), 
                "SpecGroup.AllowsWrites must be defined by each environment: " + this);
            
            bool allowsWrites = false;
            Debug.Assert(bool.TryParse(EnvironmentConfiguration.Environments[this.name][SpecGroup.AllowsWrites].Value, out allowsWrites), 
                "SpecGroup.AllowsWrites must be a boolean value.");

            return allowsWrites;
        }

        /// <summary>
        /// Gets the database credentials for the specified database.
        /// </summary>
        /// <returns>The database credentials as a Multi-level dictionary.</returns>
        /// <param name="databaseName">Database name.</param>
        public virtual MultiLevelDictionary GetDatabaseCredentials(string databaseName)
        {
            return EnvironmentConfiguration.Config["db_creds"][databaseName];
        }

        /// <summary>
        /// Gets the credentials for a specific service.
        /// </summary>
        /// <returns>The credentials as a Multi-level dictionary.</returns>
        /// <param name="credentialSet">The name of the service credentials.</param>
        /// <param name="defaultValue">The default value to be returned if the credentials do not exist.</param>
        public virtual MultiLevelDictionary GetCredentials(string credentialSet, MultiLevelDictionary defaultValue = null)
        {
            return EnvironmentConfiguration.Config.Get(credentialSet, defaultValue);
        }

        /// <summary>
        /// Returns a <see cref="System.String"/> that represents the current <see cref="Testaframe.Config.BaseEnvironment"/>.
        /// </summary>
        /// <returns>A <see cref="System.String"/> that represents the current <see cref="Testaframe.Config.BaseEnvironment"/>.</returns>
        public override string ToString()
        {
            return string.Format("[{0}]", this.GetType().Name);
        }
    }
}

