const responseHelper= {successResponse:(event,message,content={},result=true)=>{
        let success={
            statusCode:200,
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
            body:JSON.stringify({message,...errorPayload}),
        };
        return resData;
    }
}

export default responseHelper