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
            queryFn: ({remoteHostId, itemsToTransfer}) => {
                console.log("Fired createTransfer with ", remoteHostId);
                return { data: {id: 4}};
            }
        }),
        validateTransfer: builder.query({
            queryFn: ({remoteHostId}, {getState}) => {
                if (remoteHostId === 1) {
                    return { data: validateTransferData.objects[0]};
                } else {
                    return {
                        data: {
                            invalidItems: {}
                        }
                    };
                }
                // const hostById = 
            }
        }),
        getRemoteHosts: builder.query({
            queryFn: () => {
                const hostById = remoteHostData.objects.map(host => [host.id, host]);
                return {
                    data: Object.fromEntries(hostById)
                };
            },
            transformResponse: data => {
                // Map entries by id
                // const hostById = data.objects.map(host => [host.id, host]);
                // return Object.fromEntries(hostById);
            }
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