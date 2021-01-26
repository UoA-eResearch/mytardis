import React from 'react'
import makeMockStore from "../../../util/makeMockStore";
import { PureFiltersSection } from './FiltersSection';
import { schemaData,allSchemaIdsData } from '../type-schema-list/TypeSchemaList.stories';
import { Provider } from "react-redux";

export default {
  component: PureFiltersSection,
  title: 'Filters/Filters section',
  decorators: [story => <div style={{ padding: '3rem', width: "400px" }}>{story()}</div>],
  excludeStories: /.*Data$/,
};


export const filtersData = {
  types: {
    byId: {
      projects: {
        "full_name": "Project",
        attributes: {
          byId: {
            name: {
              full_name: "Name",
              id: "name",
              data_type:"STRING",
              filterable: true,
              sortable: true
            },
            createdDate: {
              full_name: "Created date",
              id: "createdDate",
              data_type: "DATETIME",
              filterable: true,
              sortable: true
            },
            institution: {
              full_name: "Institution",
              id: "institution",
              data_type: "STRING",
              filterable: true,
              sortable: true
            },
            schema: {
              full_name: "Schema",
              value: { op: "is", content: ["1"] },
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      experiments: {
        full_name: "Experiment",
        attributes: {
          byId: {
            name: {
              full_name: "Name",
              id: "name",
              
              data_type:"STRING",
              filterable: true,
              sortable: true
            },
            createdDate: {
              full_name: "Created date",
              id: "createdDate",
              data_type: "DATETIME",
              filterable: true,
              sortable: true
            },
            institution: {
              full_name: "Institution",
              id: "institution",
              data_type: "STRING",
              filterable: true,
              sortable: true
            },
            schema: {
              full_name: "Schema",
              value: { op: "is", content: ["2"] }
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      datasets: {
        full_name: "Dataset",
        attributes: {
          byId: {
            name: {
              full_name: "Name",
              id: "name",
              data_type:"STRING",
              filterable: true,
              sortable: true
            },
            createdDate: {
              full_name: "Created date",
              id: "createdDate",
              data_type: "DATETIME",
              filterable: true,
              sortable: true
            },
            institution: {
              full_name: "Institution",
              id: "institution",
              data_type: "STRING",
              filterable: true,
              sortable: true
            },
            schema: {
              full_name: "Schema",
              value: { op: "is", content: ["1"] },
              filterable: true
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      datafiles: {
        full_name: "Datafile",
        attributes: {
          byId: {
            name: {
              full_name: "Name",
              id: "name",
              data_type:"STRING",
              filterable: true,
              sortable: true
            },
            createdDate: {
              full_name: "Created date",
              id: "createdDate",
              data_type: "DATETIME",
              filterable: true,
              sortable: true
            },
            institution: {
              full_name: "Institution",
              id: "institution",
              data_type: "STRING",
              filterable: true,
              sortable: true
            },
            schema: {
              value: { op: "is", content: ["1", "2"] },
              full_name: "Schema"
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      }
    },
    allIds: ["projects", "experiments", "datasets", "datafiles"]
  },
  schemas: {
    byId: schemaData,
    allIds: allSchemaIdsData
  },
  typeSchemas: {
    projects: allSchemaIdsData,
    experiments: allSchemaIdsData,
    datasets: allSchemaIdsData,
    datafiles: allSchemaIdsData
  },
  activeFilters: {
    project: [{
      kind: "typeAttribute",
      target: ["projects", "schema"]
    }],
    experiment: [{
      kind: "typeAttribute",
      target: ["experiments", "schema"]
    }],
    dataset: [{
      kind: "typeAttribute",
      target: ["datasets", "schema"]
    }],
    datafile: [{
      kind: "typeAttribute",
      target: ["datafiles", "schema"]
    }]
  },
  isLoading: false,
  error: null
};

const makeMockStoreWithFilterSlice = (filterSlice) => (makeMockStore({filters: filterSlice}));


export const noFiltersData = Object.assign({},filtersData, {
  typeSchemas: null
})

export const loadingData = Object.assign({},filtersData, {
  isLoading: true
})

export const errorData = Object.assign({},filtersData, {
  error: "Error loading filter data"
})

export const Default = () => {
    const store = makeMockStoreWithFilterSlice(filtersData);
    return <Provider store={store}><PureFiltersSection {...filtersData} /></Provider>
};

export const NoFilters = () => {
  const store = makeMockStoreWithFilterSlice(noFiltersData);
  return <Provider store={store}><PureFiltersSection {...noFiltersData} /></Provider>
};

export const Loading = () => {
  const store = makeMockStoreWithFilterSlice(loadingData);
  return <Provider store={store}><PureFiltersSection {...loadingData} /></Provider>
};

export const Error = () => {
  const store = makeMockStoreWithFilterSlice(errorData);
  return <Provider store={store}><PureFiltersSection {...errorData} /></Provider>
};
