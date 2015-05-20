using System;
using System.Collections.Generic;

namespace Testaframe.Utilities
{
    public class MultiLevelDictionary
    {
        private Dictionary<string, MultiLevelDictionary> values = new Dictionary<string, MultiLevelDictionary>();
        private readonly string value;

        public MultiLevelDictionary(Dictionary<string, MultiLevelDictionary> dictionary)
        {
            this.values = dictionary;
            this.value = null;
        }

        public MultiLevelDictionary(string value)
        {
            this.value = value;
            this.values = null;
        }

        public string Value
        {
            get
            {
                return this.value;
            }
        }

        public MultiLevelDictionary this[string key]
        {
            get
            {
                return this.values[key];
            }
        }

        public MultiLevelDictionary Get(string key, MultiLevelDictionary value)
        {
            if(this.values.ContainsKey(key))
            {
                return this.values[key];
            }
            else
            {
                return value;
            }
        }

        public bool ContainsKey(string key)
        {
            return this.values.ContainsKey(key);
        }
    }
}

