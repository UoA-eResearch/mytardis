import React from 'react'
import makeMockStore from "../../../util/makeMockStore";
import FiltersSection from './FiltersSection';
import { schemaData,allSchemaIdsData } from '../type-schema-list/TypeSchemaList.stories';
import { Provider } from "react-redux";

export default {
  component: FiltersSection,
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
              schema: {
                value:{op:"is",content:["1"]}
            }
          }, allIds: ['schema']
        }
      },
      experiments: {
        attributes: {
          byId: {
            schema: {
              value:{op:"is",content:["2"]}
            }
          }, allIds: ['schema']
        }
      },
      datasets: {
        attributes: {
          byId: {
            schema: {
              value: {op:"is",content:["1"]}
            }
          }, allIds: ['schema']
        }
      },
      datafiles: {
        attributes: {
          byId: {
            schema: {
              value:{op:"is",content:["1","2"]}
            }
          }, allIds: ['schema']
        }
      }
    },
    allIds: ["projects","experiments","datasets","datafiles"]
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

export const loadingData = Object.assign({},filtersData, {
  isLoading: true
})

export const errorData = Object.assign({},filtersData, {
  error: "Error loading filter data"
})

export const Default = () => {
    const store = makeMockStoreWithFilterSlice(filtersData);
    return <Provider store={store}><FiltersSection /></Provider>
};

export const Loading = () => {
  const store = makeMockStoreWithFilterSlice(loadingData);
  return <Provider store={store}><FiltersSection /></Provider>
};

export const Error = () => {
  const store = makeMockStoreWithFilterSlice(errorData);
  return <Provider store={store}><FiltersSection /></Provider>
};
