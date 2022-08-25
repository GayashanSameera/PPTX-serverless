import {responseHelper,fetchDataResult,lambdaHelper} from "../helpers"
import * as payloadTemplates from "./payloadTemplates"
import  {generatedTemplate}  from "./hooks";
import {TPIP_MS_PPTX_GEN,TPIP_FN_GENERATE} from '../constants/commonConstants'
import {performance} from "perf_hooks";


import _ from "lodash";


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
        
        try {
          updatedTemplate = await generatedTemplate.generate(templateKey,payloadTemplate,fetchedData);

        } catch (error) {
          console.log(error)
        }
        
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
      const start = performance.now();
      const template =await payloadCreatorHandler.createPayload(event);
     
      const _event=event;
      const{templateKey,outPutFileName,destBucketName,destPath}=event.body;
      
      _event.body=JSON.stringify({template:JSON.stringify(template),templateKey,outPutFileName,destBucketName:JSON.stringify(destBucketName),destPath});
      //call to python service using  createPayload responce 
      await lambdaHelper.invokeR2(TPIP_MS_PPTX_GEN,TPIP_FN_GENERATE,_event);
      const duration = performance.now() - start;
      console.log('Code Execution Time',duration);
      return responseHelper.successResponse(event,'Successfully Fetched Template',template,true);
      // return invokePython(template);


    
    } catch (error) {
      
      return responseHelper.errorResponse(event,500,"create payload Failed",error);
      
    }

  
    
    
  },
}




export default payloadCreatorHandler;