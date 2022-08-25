import _, { template } from "lodash";
import fetchDataResult from "../../../helpers/fetchData";


const FORMAL_PROPOSAL1={
    "schemeName": "dfsdf",
    "templateKey": "",
    "trusteeName": {
        "text": "sample trustee",
        "styles": {
            "fontcolor": "",
            "fontSize": 3
        }
    },
    "imageOne": {
    "url": "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAADMElEQVR4nOzVwQnAIBQFQYXff81RUkQCOyDj1YOPnbXWPmeTRef+/3O/OyBjzh3CD95BfqICMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMO0TAAD//2Anhf4QtqobAAAAAElFTkSuQmCC",
    "dimensions": { "left": 1, "top": 1, "height": 3, "width": 8 }
},
    "sample_data_1": {
    "data": [{ "name": "Kamal", "age": 12 }, { "name": "Amal", "age": 22 }, { "name": "Nuwan", "age": 32 }],
    "textStyles": {
        "fontcolor": "",
        "fontSize": 3
    }
},
    "sample_data_2": [{ "name": "Kamal", "age": 12 }, { "name": "Amal", "age": 22 }, { "name": "Nuwan", "age": 32 }],
    "cashFlows": {
    "headers": ["cashflow year", "cashflow fixed", "cashflow real"],
    "row_count": 10,
    "colum_count": 3,
    "table_count_per_slide": 4,
    "dimensions": {
        "top": 1,
        "width": 0.6,
        "row_height": 0.04
    },
    "rows": [
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
},      "dataTable_rowName": false,
        "dataTtable_columnName": false,
        "dataFetch": {
            "scheme" : ["scheme_data"],
            "analytics": ["r1b", "c1"],
            "charts": ["assets","liabilities"]
}
 };
export default FORMAL_PROPOSAL1;
