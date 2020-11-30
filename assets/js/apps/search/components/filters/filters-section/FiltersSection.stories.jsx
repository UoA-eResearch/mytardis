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
              value: { op: "is", content: ["1"] },
              filterable: true,
              sortable: true
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      experiments: {
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
              value: { op: "is", content: ["2"] }
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      datasets: {
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
              value: { op: "is", content: ["1"] },
              filterable: true
            }
          }, allIds: ["name", "createdDate", "institution", "schema"]
        }
      },
      datafiles: {
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
              value: { op: "is", content: ["1", "2"] }
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
  isLoading: false,
  error: null
};

const makeMockStoreWithFilterSlice = (filterSlice) => (makeMockStore({filters:filterSlice}));


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
