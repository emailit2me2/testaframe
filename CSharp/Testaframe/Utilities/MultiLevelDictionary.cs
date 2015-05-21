using System;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Testaframe.Utilities
{
    //TODO: Expand this to not only work with JSON.
    //TODO: Add Array support.

    /// <summary>
    /// Provides a dictionary representation of JSON. 
    /// Each MultiLevelDictionary will have a Value or be a dictionary.
    /// </summary>
    public sealed class MultiLevelDictionary
    {
        private Dictionary<string, MultiLevelDictionary> values = new Dictionary<string, MultiLevelDictionary>();
        private string myKey = null;
        private readonly string value;

        /// <summary>
        /// Initializes a new instance of the <see cref="Testaframe.Utilities.MultiLevelDictionary"/> class.
        /// </summary>
        /// <param name="json">JSON formatted string to parse.</param>
        public MultiLevelDictionary(string json) : this(JsonConvert.DeserializeObject<Dictionary<string, object>>(json))
        {            
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="Testaframe.Utilities.MultiLevelDictionary"/> class.
        /// </summary>
        /// <param name="dictionary">Dictionary of JSON</param>
        private MultiLevelDictionary(Dictionary<string, object> dictionary) : this("root", dictionary)
        {            
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="Testaframe.Utilities.MultiLevelDictionary"/> class.
        /// </summary>
        /// <param name="key">The key of this object.</param>
        /// <param name="dictionary">The sub dictionary of JSON.</param>
        private MultiLevelDictionary(string key, Dictionary<string, object> dictionary)
        {
            this.myKey = key;
            this.value = null;
            foreach(var pair in dictionary)
            {
                JContainer jContainer = pair.Value as JContainer;
                if(jContainer != null)
                {
                    this.values.Add(pair.Key, new MultiLevelDictionary(pair.Key, jContainer.ToString()));
                }
                else
                {
                    this.values.Add(pair.Key, new MultiLevelDictionary(pair.Key, pair.Value.ToString()));   
                }
            }
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="Testaframe.Utilities.MultiLevelDictionary"/> class.
        /// </summary>
        /// <param name="key">The key of this object.</param>
        /// <param name="value">The value of the object.</param>
        private MultiLevelDictionary(string key, string value)
        {
            this.myKey = key;
            this.value = value;
            this.values = null;
        }

        /// <summary>
        /// Gets the singular value.
        /// </summary>
        /// <value>The value.</value>
        public string Value
        {
            get
            {
                return this.value;
            }
        }

        /// <summary>
        /// Gets the <see cref="Testaframe.Utilities.MultiLevelDictionary"/> with the specified key.
        /// </summary>
        /// <param name="key">The key.</param>
        public MultiLevelDictionary this[string key]
        {
            get
            {
                return this.values[key];
            }
        }

        /// <summary>
        /// Get the specified key with a default value should the key not exist.
        /// </summary>
        /// <param name="key">The key.</param>
        /// <param name="defaultValue">The default value.</param>
        public string Get(string key, string defaultValue)
        {
            if(this.values.ContainsKey(key))
            {
                return this.values[key].ToString();
            }
            else
            {
                return defaultValue;
            }
        }

        /// <summary>
        /// Get the specified key with a default value should the key not exist.
        /// </summary>
        /// <param name="key">The key.</param>
        /// <param name="defaultValue">The default value.</param>
        public MultiLevelDictionary Get(string key, MultiLevelDictionary defaultValue)
        {
            if(this.values.ContainsKey(key))
            {
                return this.values[key];
            }
            else
            {
                return defaultValue;
            }
        }

        /// <summary>
        /// Does this level of the dictionary contain the key.
        /// </summary>
        /// <returns><c>true</c>, if key was contained, <c>false</c> otherwise.</returns>
        /// <param name="key">The key.</param>
        public bool ContainsKey(string key)
        {
            return this.values.ContainsKey(key);
        }

        /// <summary>
        /// Returns a <see cref="System.String"/> that represents the current <see cref="Testaframe.Utilities.MultiLevelDictionary"/>.
        /// </summary>
        /// <returns>A <see cref="System.String"/> that represents the current <see cref="Testaframe.Utilities.MultiLevelDictionary"/>.</returns>
        public override string ToString()
        {
            string str = null;
            if (this.value != null)
            {
                str = this.value.ToString();
            }
            else
            {
                StringBuilder builder = new StringBuilder();
                builder.Append(this.myKey + ":{");
                foreach(var entry in this.values)
                {
                    builder.Append(entry.ToString());
                }
                builder.Append("}");
                str = builder.ToString();
            }

            return str;
        }
    }
}

