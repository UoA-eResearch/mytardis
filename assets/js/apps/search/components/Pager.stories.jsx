import React from "react";
import { PurePager } from "./Pager";
import { action } from "@storybook/addon-actions";

export default {
    component: PurePager,
    title: "Pager",
    decorators: [story => <div style={{ padding: "3rem" }}>{story()}</div>],
    excludeStories: /.*Data$/
};

export const paginationData = {
    pageNum: 5,
    pageSize: 50,
    totalPages: 10,
    handlePageNumChange: action("Page number change")
};

export const Default = () => (
    <PurePager {...paginationData} />
);