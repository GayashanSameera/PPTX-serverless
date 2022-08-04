import _, { template } from "lodash";
import fetchDataResult from "../fetchData";

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
    sample_data_1: {
    data: [{ name: "Kamal", age: 12 }, { name: "Amal", age: 22 }, { name: "Nuwan", age: 32 }],
    textStyles: {
        fontcolor: "",
        fontSize: 3,
    }
},
    sample_data_2: [{ name: "Kamal", age: 12 }, { name: "Amal", age: 22 }, { name: "Nuwan", age: 32 }],
    cashFlows: {
    headers: ["cashflow year", "cashflow fixed", "cashflow real"],
    row_count: 10,
    colum_count: 3,
    table_count_per_slide: 4,
    dimensions: {
        top: 1,
        width: 0.6,
        row_height: 0.04,
    },
    rows: [
        {
            "cashflow_year": "2020", "cashflow_fixed": "1", "cashflow_real": "123123"
        },
        {
            "cashflow_year": "2020", "cashflow_fixed": "2", "cashflow_real": "123123"
        },
        {
            "cashflow_year": "2020", "cashflow_fixed": "3", "cashflow_real": "123123"
        },
        {
            "cashflow_year": "2020", "cashflow_fixed": "4", "cashflow_real": "123123"
        }
    ]
},      dataTable_rowName: False,
        dataTtable_columnName: False,
        dataFetch: {
            scheme : ["scheme_data"],
            analytics: ["r1b", "c1"],
            charts: ["assets","liabilities"]
}
 };

// export default async(event)=>{
//     const fetchDataResult=fetchDataResult.fetchData(event,formalProposal1)


//     return formalProposal1
// }