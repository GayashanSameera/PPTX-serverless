const formalProposal1={
    schemeName: 'sample scheme',
    templateKey: 'formal_proposal_1',
    trusteeName: {
        text: 'sample trustee',
        styles: {
            fontcolor: '',
            fontSize: 3,
        }
    },
    imageOne: {
    url: "../1.png",
    dimensions: { left: 1, top: 1, height: 3, width: 8 }
},

 };

export default async(event)=>{

    return formalProposal1
}