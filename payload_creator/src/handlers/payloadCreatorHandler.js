import {responseHelper,fetchDataResult,lambdaHelper} from "../helpers"
import * as payloadTemplates from "./payloadTemplates"
import  {generatedTemplate}  from "./hooks";
import {TPIP_MS_PPTX_GEN,TPIP_FN_GENERATE} from '../constants/commonConstants'
import imageToBase64 from "image-to-base64";
import _ from "lodash";
import aws from 'aws-sdk';


// const setBaseImage=(obj)=>{
//   console.log("objni",obj);

//   // iterate over the properties
//   for (let propertyName in obj) {
//     if(propertyName === 'url' && obj['url'] !== null){
//       console.log("objniurk", obj[propertyName])
//       obj[propertyName]=imageToBase64('obj[propertyName]')
//       // _.set(obj,propertyName,  imageToBase64(obj[propertyName]) )
//     }
//     // any object that is not a simple value
//     if (obj[propertyName] !== null && typeof obj[propertyName] === 'object') {
//       // recurse into the object and write back the result to the object graph
//       obj[propertyName] = setBaseImage(obj[propertyName]);
    
//   }
// }

// console.log("obj",obj)
// return obj;

// }
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
      // console.log("gggggggggggggg",updatedTemplate);

      //   //BASE-64
      //   const updatedTemp=setBaseImage(updatedTemplate);

        // console.log('ddddddddddddddddddddddddddd',updatedTemp);
      // for(let prop in updatedTemplate.content ){
      //   if(prop==='imageOe' && updatedTemplate.content[prop].url){
      //     _.set(updatedTemplate.content,updatedTemplate[prop].url,)
      //   }
      // }
      // imageToBase64(generatedTemplate["url"]) // Path to the image
    // . then(
    //     (response) => {
    //         console.log(response);
    //     }
    //   )
    // .catch(
    //     (error) => {
    //         console.log(error); 
    //     }
    // )

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
      console.log('llllllllllllllllll',template);
      const _event=event;
      _event.body={template};
      lambdaHelper.invokeR2(TPIP_MS_PPTX_GEN,TPIP_FN_GENERATE,_event);
      return responseHelper.successResponse(event,'Successfully Fetched Template',template,true);
      // return invokePython(template);


    
    } catch (error) {
      return responseHelper.errorResponse(event,500,"create payload Failed")
    }

  
    
    //call to python service using  createPayload responce 
  },
}

// const invokePython=(template)=> {
//   console.log('mmmmmmmmmmmmmmmmmmmmmm',template);
// const lambda = new aws.Lambda({
//   region: 'eu-west-2' //change to your region
// });

// lambda.invoke({
  
//   FunctionName: 'generate',
//   Payload: JSON.stringify(template,null,2) // pass params
  
  
// }, function(error, data) {
//   console.log('bbbbbbbbbbbbbbbbbbbb',data);
//   if (error) {
//       console.log("error",error,data);
//     context.done('error', error);
//     console.log('dfdsfsdffffffffffffffffff',data);
//   }
//   if(data.Payload){
//    context.succeed(data.Payload)
//   }
// });
// }


export default payloadCreatorHandler;