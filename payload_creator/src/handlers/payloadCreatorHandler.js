import {responseHelper,fetchDataResult} from "../helpers"
import * as payloadTemplates from "./payloadTemplates"
import  {generatedTemplate}  from "./hooks";

const payloadCreatorHandler={
  

   createPayload:async (event)=>{
    let updatedTemplate={};
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
       //read selected template
       
      const payloadTemplate= payloadTemplates[templateKey]
      
     
      // fetch data using template keys
      const fetchedData= await fetchDataResult.fetchData(event,payloadTemplate);
      //hooks for update template using fetched data
        
        updatedTemplate = await generatedTemplate.generate(templateKey,payloadTemplate,fetchedData);
       
  
      // return responseHelper.successResponse(event,'Successfully Fetched Template',updatedTemplate,true)
      return updatedTemplate;

    }catch(error){

      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   },


   generatePPTX: async (event) => {
    
  
    
    //createPayload
    //get responce from createPayload
    try {
      const template =await payloadCreatorHandler.createPayload(event);
      return responseHelper.successResponse(event,'Successfully Fetched Template',template,true)

    } catch (error) {
      return responseHelper.errorResponse(event,500,"create payload Failed")
    }

  
    
    //call to python service using  createPayload responce 


  }


}


export default payloadCreatorHandler;