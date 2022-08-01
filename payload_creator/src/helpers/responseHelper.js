module.exports={
    successResponse:(event,message,content={},result=true)=>{
        let success={
            statusCode:200,
            header:'',
            body:JSON.stringify({
            result,
            message,
            content,
            }),
            
        }
        return success;
    } ,


    errorResponse:(event,statusCode,message,err,errorPayload)=>{
        const resData={
            statusCode,
            header:"",
            body:JSON.stringify({message,...errorPayload}),
        };
        return resData;
    }
}