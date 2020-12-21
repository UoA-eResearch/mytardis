import React, { Fragment, useCallback } from "react";
import PropTypes from "prop-types";
import { Badge, Button } from "react-bootstrap";
import "./FilterSummaryBox.css";
import { useDispatch, useSelector } from "react-redux";
import { 
    resetFilters, 
    schemaParamFilterValueSelector, 
    schemaParamSelector, 
    schemaSelector, 
    schemaTypeSelector,
    typeAttrSelector, 
    typeSelector,
    typeAttrFilterValueSelector
} from "../filters/filterSlice";
import { runSearch } from "../searchSlice";

function InvalidFilterBadge() {
    return <Badge variant="secondary">(Invalid filter)</Badge>;
}

function FilterBadge({fieldName, value}) {
    return <div className="filter-summary-box__badge-group">
        <Badge variant="secondary" className="filter-summary-box__badge">{fieldName}</Badge>
        {value.map(({op, content}) => 
            <>
                <Badge variant="info" className="filter-summary-box__badge">{op}</Badge>
                <Badge variant="secondary" className="filter-summary-box__badge">{content}</Badge>
            </>
        )}
    </div>;

}

FilterBadge.propTypes = {
    typeId: PropTypes.string.isRequired,
    fieldName: PropTypes.string.isRequired,
    value: PropTypes.arrayOf(PropTypes.shape({
        op: PropTypes.string.isRequired,
        content: PropTypes.string.isRequired
    })).isRequired
};

function SchemaParameterFilterBadge({fieldInfo}) {
    const schemaId = fieldInfo.target[0], parameterId = fieldInfo.target[1];
    const typeId = useSelector(state => schemaTypeSelector(state.filters, schemaId));
    const fullFieldName = useSelector(state => {
        const type = typeSelector(state.filters, typeId);
        const schema = schemaSelector(state.filters, schemaId); 
        const schemaParam = schemaParamSelector(state.filters, schemaId, parameterId);
        if (!type || !schema || !schemaParam) {
            return "";
        } else {
            return `${type.full_name}.${schema.schema_name}.${schemaParam.full_name}`; 
        }
    });
    if (fullFieldName === "") {
        return <InvalidFilterBadge />;
    } else {
        const filterValue = useSelector(
            state => schemaParamFilterValueSelector(state.filters, schemaId, parameterId)
        );
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />;
    }
}


function TypeAttributeFilterBadge({fieldInfo}) {
    const typeId = fieldInfo.target[0], attributeId = fieldInfo.target[1];
    const fullFieldName = useSelector(state => {
        // Remove the extra s
        const type = typeSelector(state.filters, typeId.substring(0, typeId.length - 1));
        const attribute = typeAttrSelector(state.filters, typeId, attributeId);
        if (!type || !attribute) {
            return "";
        } else {
            return `${type.full_name}.${attribute.full_name}`;
        }
    });
    if (fullFieldName === "") {
        return <InvalidFilterBadge />;
    } else {
        const filterValue = useSelector(
            state => typeAttrFilterValueSelector(state.filters, typeId, attributeId)
        );
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />;
    }
}

function getFilterBadge(filterKind) {
    switch (filterKind) {
        case "typeAttribute":
            return TypeAttributeFilterBadge;
            break;
        case "schemaParameter":
            return SchemaParameterFilterBadge;
            break;
        default:
            break;
    } 

}

function FilterSummaryFilterList({activeFilters = []}) {
    const hasActiveFilters = activeFilters.length > 0;
    if (!hasActiveFilters) {
        return <p>Use options on the left to narrow down your results.</p>;
    } else {
        return <div className="h5">
            {activeFilters.map((filter, index) => {
                const isLastFilter = index === activeFilters.length - 1;
                const FilterBadge = getFilterBadge(filter.kind);
                return <Fragment key={filter.kind + filter.target.join(",")}>
                    <FilterBadge fieldInfo={filter} />
                    {!isLastFilter ? <Badge variant="info" className="filter-summarybox__badge--separator">AND</Badge> : null}
                </Fragment>;
            })
            }
        </div>;
    }
}

export function PureFilterSummaryBox({activeFilters = [], onResetFilters}) {

    const hasActiveFilters = activeFilters.length > 0;
    return (
        <div className="card" style={{padding: "1rem"}}>
            <div className="card-body d-flex">
                <div className="flex-grow-1">
                    <FilterSummaryFilterList activeFilters={activeFilters} />
                </div>
                <div>
                    <Button className="ms-1" onClick={onResetFilters} variant={hasActiveFilters ? "primary" : "outline-secondary"}>Reset</Button>
                </div>
            </div>
        </div>
    );
}

export default function FilterSummaryBox() {
    const activeFiltersByTypeId = useSelector(state => state.filters.activeFilters);
    const activeFilters = [];
    for (const typeId in activeFiltersByTypeId) {
        activeFiltersByTypeId[typeId].forEach(filter => {
            activeFilters.push(filter);
        })
    }
    const dispatch = useDispatch();
    const handleFilterResetClick = useCallback(
        () => {
            dispatch(resetFilters());
            dispatch(runSearch());
        },
        [dispatch]
    );
    return (
        <PureFilterSummaryBox activeFilters={activeFilters} onResetFilters={handleFilterResetClick} />
    );
}
