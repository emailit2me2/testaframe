using System;
using Testaframe.Config;
using Testaframe.Data;

namespace Testaframe
{
    public abstract class AutomationBase
    {
        protected const BaseEnvironment ENVIRONMENT = null;
        protected const BaseOSBrowserEnvironment OSBROWSER = null;

        public AutomationBase()
        {
            
        }

        public abstract DataBuilder Data
        {
            get;
            protected set;
        }
    }
}

