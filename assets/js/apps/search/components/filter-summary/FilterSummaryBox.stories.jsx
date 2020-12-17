import React from "react";
import { PureFilterSummaryBox } from "./FilterSummaryBox";

export default {
    component: PureFilterSummaryBox,
    title: "Filter summary box",
    parameters: { actions: { argTypesRegex: "^on.*" } },
    decorators: [story => <div style={{ padding: "3rem" }}>{story()}</div>]
};

const Template = (args) => <PureFilterSummaryBox {...args}/>;

export const Default = Template.bind({});
Default.args = {
    activeFilters: [
        {
            typeId: "experiment",
            field: "Description",
            op: "contains",
            content: "Hello"
        },
        {
            typeId: "project",
            field: "Title",
            op: "contains",
            content: "OK",
        }
    ]
};