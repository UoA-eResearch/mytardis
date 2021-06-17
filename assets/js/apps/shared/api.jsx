import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import Cookies from "js-cookie";
// Not yet implemented as an API, hence mock data here.
import siteData from "./mockSiteApi.json";
import {  } from "./";

export const myTardisApi = createApi({
    reducerPath: "myTardisApi",
    baseQuery: fetchBaseQuery({ 
        baseUrl: "/api/v1/",
        prepareHeaders: (headers) => {
            const csrftoken = Cookies.get("csrftoken");
            if (csrftoken) {
                headers.set("X-CSRFToken", csrftoken);
            }
            return headers;
        },
        fetchFn: window.fetch
    }),
    endpoints: builder => ({
        getObjectById: builder.query({
            query: ({name, id}) => `${name}/${id}/`
        }),
        getSite: builder.query({
            queryFn: () => {
                return {
                    data: siteData
                };
            }
        }),
        getEndpoints: builder.query({
            queryFn: () => {
                return {
                    data: 
                }
            }
        })
    })
});

export const { useGetObjectByIdQuery, useGetSiteQuery } = myTardisApi;