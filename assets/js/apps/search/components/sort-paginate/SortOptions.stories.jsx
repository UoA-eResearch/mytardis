import React from "react";
import { PureSortOptions } from "./SortOptions";
import { SORT_ORDER } from "../searchSlice";


export default {
    component: PureSortOptions,
    title: "Sort options",
    decorators: [story => <div style={{ padding: "3rem" }}>{story()}</div>],
    excludeStories: /.*Data$/
};

export const sortData = {
    attributesToSort: [
        {
            id: "name",
            full_name: "Name",
            order: SORT_ORDER.ascending,
            isActive: false
        },
        {
            id: "createdDate",
            full_name: "Ingestion date",
            order: SORT_ORDER.ascending,
            isActive: false
        },
        {
            id: "institution",
            full_name: "Institution",
            order: SORT_ORDER.ascending,
            isActive: false
        }
    ]
};

export const activeSortData = Object.assign({}, sortData, {
    attributesToSort: [
        {
            id: "name",
            full_name: "Description",
            order: SORT_ORDER.ascending,
            isActive: true
        },
        {
            id: "createdDate",
            full_name: "Created date",
            order: SORT_ORDER.descending,
            isActive: false
        }
    ]
});

export const Default = () => (
    <PureSortOptions {...sortData} />
);

export const SortActive = () => (
    <PureSortOptions {...activeSortData} />
);