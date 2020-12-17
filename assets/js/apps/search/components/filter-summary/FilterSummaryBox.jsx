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
    return <Badge variant="secondary">(Invalid filter)</Badge>
}

function FilterBadge({fieldName, op, content}) {
    return <>
        <Badge variant="secondary" className="filter-summary-box__badge">{fieldName}</Badge>
        <Badge variant="secondary" className="filter-summary-box__badge">{op}</Badge>
        <Badge variant="secondary" className="filter-summary-box__badge">{content}</Badge>
    </>;

}

FilterBadge.propTypes = {
    typeId: PropTypes.string.isRequired,
    fieldName: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired
};

function SchemaParameterFilterBadge({fieldInfo}) {
    const schemaId = fieldInfo.target[0], parameterId = fieldInfo.target[1];
    const schemaName = useSelector(state => {
        const schema = schemaSelector(state.filters, schemaId); 
        return schema ? schema.schema_name : null;
    });
    const fieldName = useSelector(state => {
        const schemaParam = schemaParamSelector(state.filters, schemaId, parameterId);
        return schemaParam ? schemaParam.full_name : null;
    });

    const filterValue = useSelector(state => schemaParamFilterValueSelector(state.filters, schemaId, parameterId));
    const typeId = useSelector(state => schemaTypeSelector(state.filters, schemaId));
    const typeName = useSelector(state => {
        const type = typeSelector(state.filters, typeId);
        return type ? type.full_name : null;
    });
    console.log("Hello" + typeName + schemaName + fieldName);
    if (!typeName || !schemaName || !fieldName) {
        return <InvalidFilterBadge />;
    } else {
        const fullFieldName = `${typeName}.${schemaName}.${fieldName}`;
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />;
    }
}


function TypeAttributeFilterBadge({fieldInfo}) {
    const typeId = fieldInfo.target[0], attributeId = fieldInfo.target[1];
    const typeName = useSelector(state => {
        // Remove the extra s
        const typeMetadata = typeSelector(state.filters, typeId.substring(0, typeId.length - 1));
        console.log("Type metadata is " + typeMetadata);
        return typeMetadata ? typeMetadata.full_name : null;
    });
    const fieldName = useSelector(state => {
        const attribute = typeAttrSelector(state.filters, typeId, attributeId);
        return attribute ? attribute.full_name : null;
    });
    const filterValue = useSelector (state => typeAttrFilterValueSelector(state.filters, typeId, attributeId));
    if (!typeName || !fieldName) {
        return <InvalidFilterBadge />;
    } else {
        const fullFieldName = `${typeName}.${fieldName}`;
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />
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
                let ApplicableFilterBadge;
                switch (filter.kind) {
                    case "typeAttribute":
                        ApplicableFilterBadge = TypeAttributeFilterBadge;
                        break;
                    case "schemaParameter":
                        ApplicableFilterBadge = SchemaParameterFilterBadge;
                        break;
                    default:
                        break;
                } 
                return <Fragment key={filter.kind + filter.target.join(",")}>
                    <ApplicableFilterBadge fieldInfo={filter} />
                    {!isLastFilter ? <Badge variant="info" className="filter-summarybox__badge--conjunctive">AND</Badge> : null}
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
                    <Button className="ms-1" onClick={onResetFilters} variant={hasActiveFilters ? "primary" : "outline-secondary"}>Reset filters</Button>
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
