import { lambdaHelper, responseHelper } from "../helpers"

const eventMiddleware=async (event,...middlewares)=>{
    if(event.source==='serveless-warmup'){
        console.log('warmup-lamda is warm')
        return responseHelper.successResponse(event,'success');
    }
    
    let result=null;
    if(typeof event.body==="string"){
        event.body=JSON.parse(event.body);
    }

    lambdaHelper.intializeEvent(event);

    try{
        for(let middleware of middlewares){
            result=await middleware(event);
        }
        return result;
    }catch(error){
        if(error.message==='400')
        return responseHelper.errorResponse(event,400,"invalid parameters");
        if(error.message==='401')
        return responseHelper.errorResponse(event,401,'unauthorized')
        if(error.message==='505')
        return responseHelper.errorResponse(event,505,'invalid')
    }
}


export {
    eventMiddleware,
};
     