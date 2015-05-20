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
        protected readonly string Name = "";
        protected readonly string ExecutableJS = "";
        protected EnvironmentConfiguration config;

        public BaseEnvironment(EnvironmentConfiguration config)
        {
            this.config = config;
        }

        public abstract PageFactory PrepareForService();

        public abstract void TeardownForService();

        public DataBuilder CreateDataBuilder()
        {
            throw new NotImplementedException("Must be overidden.");
        }
            
        public string GetHost(string hostName)
        {
            string host = this.config.Environments[this.Name][SpecGroup.Hosts][hostName][SpecKey.Host].Value;
            return host;
        }

        public string GetPort(string hostName)
        {
            string port = this.config.Environments[this.Name][SpecGroup.Hosts][hostName].Get(
                SpecKey.Port, new MultiLevelDictionary(string.Empty)).Value;
            return port;
        }

        public string GetUrl(string hostName)
        {
            string host = GetHost(hostName);
            string port = GetPort(hostName);
            return this.config.Environments[this.Name][SpecGroup.Hosts][hostName][SpecKey.UrlTemplate].Value.FormatEx(
                new KeyValuePair<string, string>[]
                { new KeyValuePair<string, string>("host", host),
                  new KeyValuePair<string, string>("port", port)
                });
        }

        public bool AllowsWrites()
        {
            Debug.Assert(this.config.Environments[this.Name].ContainsKey(SpecGroup.AllowsWrites), 
                "SpecGroup.AllowsWrites must be defined by each environment: " + this);
            
            bool allowsWrites = false;
            Debug.Assert(bool.TryParse(this.config.Environments[this.Name][SpecGroup.AllowsWrites].Value, out allowsWrites), 
                "SpecGroup.AllowsWrites must be a boolean value.");

            return allowsWrites;
        }

        public void AssertEnvironmentAllowsWrites()
        {
            if (!AllowsWrites())
            {
                //TODO: Need to uncover how to actually use the Selenium package.
                //throw new SkipTest();
            }
        }

        public override string ToString()
        {
            return string.Format("[{0}]", this.GetType().Name);
        }
    }
}

