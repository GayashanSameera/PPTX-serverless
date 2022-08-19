import Joi from "@hapi/joi";
import { join } from "lodash";

const requestPayloadCreatorSchema=Joi.object().keys({
    schemeId:Joi.string().required(),
    scheme:Joi.string().required(),
    templateKey:Joi.string().required(),
    outPutFileName:Joi.string().required(),
    destBucketName:Joi.string().required(),
    destPath:Joi.string().required(),
    templateKey:Joi.string().required(),
    
});


const responsePayloadCreatorSchema=Joi.object().keys({
    // schemeId:Joi.string().required(),
    // scheme:Joi.string().required(),
    // templateKey:Joi.string().required(),
    // outPutFileName:Joi.string().required(),
    // destBucketName:Joi.string().required(),
    // destPath:Joi.string().required(),
    schemeName:Joi.string().required(),
    templateKey:Joi.string().required(),
    trusteeName:Joi.object({
        text:Joi.string().required(),
        styles:Joi.object().required(), }).required(),
    imageOne:Joi.string().base64().required(),
    sample_data_1:Joi.object({
        data:Joi.array().items(Joi.string().required(),Joi.number().required()),
        textStyles:Joi.object().required(),}).required(),
    sample_data_2:Joi.array().items({
        name:Joi.string().required(),
        age:Joi.number().required(),
    }),
    cashFlows:Joi.object({
        headers:Joi.array().items(Joi.string()).required(),
        row_count:Joi.number().required(),
        colum_count:Joi.number().required(),
        table_count_per_slide:Joi.number().required(),
        dimensions:Joi.object().required(),
        rows:Joi.array().items().required()
    }),
    dataTable_rowName:Joi.boolean().required(),
    dataTtable_columnName:Joi.boolean().required(),
    dataFetch:Joi.object({
        scheme:Joi.array().items().required(),
        charts:Joi.array().items().required(),
        analytics:Joi.array().items().required(),
    })
});

const payloadCreatorMiddleware={

generatePPTXValidator:(event)=>{
    if(!event.body) throw Error("400");

    const {schemeName,templateKey,trusteeName,text,
        styles,imageOne,sample_data_1,sample_data_2,
        data,age,name,cashFlows,headers,row_count,
        colum_count,table_count_per_slide,dimensions,rows,
    dataTable_rowName,dataTtable_columnName,dataFetch,scheme,charts,analytics}=event

    const {error}=responsePayloadCreatorSchema.validate({
        schemeName,templateKey,trusteeName,text,
        styles,imageOne,sample_data_1,sample_data_2,
        data,age,name,cashFlows,headers,row_count,
        colum_count,table_count_per_slide,dimensions,rows,
    dataTable_rowName,dataTtable_columnName,dataFetch,scheme,charts,analytics,
});
    if(error) throw Error ('400');
},

requestPPTXValidator:(event)=>{
    if(!event.body) throw Error('400');
    

    const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath}=event.body
    const {error}=requestPayloadCreatorSchema.validate({
        
        schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath,
    });
    if(error) throw Error('400');
    


}
}

export default payloadCreatorMiddleware;