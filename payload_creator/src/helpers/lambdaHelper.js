import commonConstants from "../constants";
import _ from "lodash";
import AWS from 'aws-sdk';

const lambda=new AWS.Lambda();
const {B2B_AUTH}=commonConstants;
const {STAGE}=process.env;

let _event={};
const lambdaHelper={
    intializeEvent:event=>{
        _event=event;
    },
    invokeR2:async(ms,fn,payload=null)=>{
        payload={..._event,...payload,permission:B2B_AUTH};
        const params={FunctionName:`${ms}-${STAGE}-${fn}`,InvocationType: 'RequestResponse',
        LogType: 'Tail',};
        

        if(!_.isEmpty(payload)){
            params.Payload=JSON.stringify(payload);
            
        }
        
        const{Payload} =await lambda.invoke(params).promise();
        
        const {statusCode=null,body=null}=JSON.parse(Payload);
        if(!statusCode){
            throw Error('Something Went Wrong While invoking Lambda Request-Response')
        }
        const _body=JSON.parse(body);
        
        
        if(statusCode===200||statusCode===201){
            return _body.content ? _body.content : _body;
        }
        if(_body&&_body.message){
            throw Error(_body.message)
        }
        throw Error('Something Went Wrong While invoking Lambda Request-Response')

    },
    
}




export default lambdaHelper;