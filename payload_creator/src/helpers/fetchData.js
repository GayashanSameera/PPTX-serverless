//move to helpers

import _ from "lodash";
const getFetchData={
    scheme:async(event)=>{},
    analytics:async(event)=>{},
    charts:async(event)=>{}};


const fetchDataResult={
    fetchData:async(event,template)=>{
        const responseDataArray={};
        const fetchDataObject=_.get(template,'dataFetch',{});
        if(_.has(fetchDataObject,'scheme'))
        responseDataArray.scheme=getFetchData.scheme(event);
        if(_.has(fetchDataObject,'analytics'))
        responseDataArray.analytics=getFetchData.analytics(event);
        if(_.has(fetchDataObject,'charts'))
        responseDataArray.charts=getFetchData.charts(event);
    }
};

export default fetchDataResult;