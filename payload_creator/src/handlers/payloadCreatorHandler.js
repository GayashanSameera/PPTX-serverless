import responseHelper from "../helpers"


const payloadCreatorHandler={
   createPayload:()=>{
    
    try{
      if(event=='success')
      responseHelper.successResponse()

    }catch{
      responseHelper.errorResponse()

    }
   } 
}
export default payloadCreatorHandler;