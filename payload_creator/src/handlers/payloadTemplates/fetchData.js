import _ from "lodash";
const getFetchData={
    scheme:async(event)=>{},
    analytics:async(event)=>{},
    charts:async(event)=>{}};


const fetchDataResult={
    fetchData:async(event,template)=>{
        const responseDataArray={};
        const fetchDataArray=_.get(template,'dataFetch',{});
        if(_.has(fetchDataArray,'scheme'))
        responseDataArray.scheme=getFetchData.scheme(event);
        if(_.has(fetchDataArray,'analytics'))
        responseDataArray.analytics=getFetchData.analytics(event);
        if(_.has(fetchDataArray,'charts'))
        responseDataArray.charts=getFetchData.charts(event);
    }
};

export default fetchDataResult;