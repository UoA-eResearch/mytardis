import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import Cookies from "js-cookie";
// Not yet implemented as an API, hence mock data here.
import siteData from "./mockSiteApi.json";
import remoteHostData from "./mockRemoteHostApi.json";
import validateTransferData from "./mockValidateTransferApi.json";

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
        createTransfer: builder.mutation({
            query: ({remoteHostId, items = {}}) => ({
                url: "/globus_transfer/",
                method: "POST",
                body: Object.assign({
                    "remote_host": remoteHostId
                }, items)
            })
        }),
        validateTransfer: builder.query({
            query: ({remoteHostId, items = {}}) => ({
                url: "/globus_transfer_validate/",
                method: "POST",
                body: { 
                    "remote_host": remoteHostId,
                    items
                }
            }),
            // queryFn: ({remoteHostId}, {getState}) => {
            //     if (remoteHostId === 1) {
            //         return { data: validateTransferData.objects[0]};
            //     } else {
            //         return {
            //             data: {
            //                 invalidItems: {}
            //             }
            //         };
            //     }
            //     // const hostById = 
            // }
        }),
        getRemoteHosts: builder.query({
            query: () => "/globus_remotehost/",
            transformResponse: res => res.objects
        })
    })
});

export const { 
    useGetObjectByIdQuery, 
    useGetSiteQuery, 
    useGetRemoteHostsQuery, 
    useValidateTransferQuery, 
    useCreateTransferMutation
} = myTardisApi;