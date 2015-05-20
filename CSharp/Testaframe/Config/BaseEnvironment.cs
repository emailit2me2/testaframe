using System;
using Testaframe.Page;
using Testaframe.Data;
using Testaframe.Utilities;
using System.Collections.Generic;
using System.Diagnostics;

namespace Testaframe.Config
{
    public abstract class BaseEnvironment
    {
        protected readonly string name = "";
        protected readonly string executableJS = "";

        public string ExecutableJS
        {
            get
            {
                return this.executableJS;
            }
        }

        public abstract PageFactory PrepareForService();

        public abstract void TeardownForService();

        public DataBuilder CreateDataBuilder()
        {
            throw new NotImplementedException("Must be overidden.");
        }
            
        public string GetHost(string hostName)
        {
            string host = EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName][SpecKey.Host].Value;
            return host;
        }

        public string GetPort(string hostName)
        {
            string port = EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName].Get(
                SpecKey.Port, string.Empty);
            return port;
        }

        public string GetUrl(string hostName)
        {
            string host = GetHost(hostName);
            string port = GetPort(hostName);
            return EnvironmentConfiguration.Environments[this.name][SpecGroup.Hosts][hostName][SpecKey.UrlTemplate].Value.Format(
                new Dictionary<string, string>() {
                {"host", host},
                {"port", port}
            });
        }

        public bool AllowsWrites()
        {
            Debug.Assert(EnvironmentConfiguration.Environments[this.name].ContainsKey(SpecGroup.AllowsWrites), 
                "SpecGroup.AllowsWrites must be defined by each environment: " + this);
            
            bool allowsWrites = false;
            Debug.Assert(bool.TryParse(EnvironmentConfiguration.Environments[this.name][SpecGroup.AllowsWrites].Value, out allowsWrites), 
                "SpecGroup.AllowsWrites must be a boolean value.");

            return allowsWrites;
        }
            
        public MultiLevelDictionary GetDatabaseCredentials(string databaseName)
        {
            return EnvironmentConfiguration.Config["db_creds"][databaseName];
        }
            
        public MultiLevelDictionary GetCredentials(string credentialSet, MultiLevelDictionary defaultValue = null)
        {
            return EnvironmentConfiguration.Config.Get(credentialSet, defaultValue);
        }

        public override string ToString()
        {
            return string.Format("[{0}]", this.GetType().Name);
        }
    }
}

