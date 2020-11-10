import React from "react";
import { PureSortOptionsList } from "./SortOptionsList";
import { SORT_ORDER } from "../searchSlice";


export default {
    component: PureSortOptionsList,
    title: "Sort options list",
    decorators: [story => <div style={{ padding: "3rem" }}>{story()}</div>],
    parameters: { actions: { argTypesRegex: '^on.*' } },
    excludeStories: /.*Data$/
};

export const sortData = [
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
];

export const activeSortData = [
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
];

const Template = (args) => <PureSortOptionsList {...args} />;

export const Default = Template.bind({});
Default.args = { attributesToSort: sortData };

export const SortActive = Template.bind({});
SortActive.args = { attributesToSort: activeSortData };