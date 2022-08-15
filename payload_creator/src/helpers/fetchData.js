//move to helpers

import _ from "lodash";
const getFetchData={
    scheme:async(event)=>{},
    analytics:async(event)=>{},
    charts:async(event)=>{}};


const fetchDataResult={
    fetchData:async(event,template)=>{
        console.log('fetchDataResult template',template );
        const responseDataArray={};
        const fetchDataObject=_.get(template,'dataFetch',{});
        console.log('fetchDataResult fetchDataObject',fetchDataObject );
        console.log('fetchDataResult has ',_.has(fetchDataObject,'scheme') );
        if(_.has(fetchDataObject,'scheme'))
        responseDataArray.scheme=getFetchData.scheme(event);
        if(_.has(fetchDataObject,'analytics'))
        responseDataArray.analytics=getFetchData.analytics(event);
        if(_.has(fetchDataObject,'charts'))
        responseDataArray.charts=getFetchData.charts(event);
        console.log('fetchDataResult responseDataArray',responseDataArray );
        return responseDataArray;
    }
};

export default fetchDataResult;