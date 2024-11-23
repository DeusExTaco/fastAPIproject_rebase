import React from 'react';
import { Input } from "@material-tailwind/react";
import { createPortal } from 'react-dom';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Calendar } from 'lucide-react';

const DROPDOWN_HEIGHT = 360;
const SPACING = 8;

interface Position {
    top: number;
    left: number;
    direction: 'up' | 'down';
}

type Direction = 'up' | 'down';

interface DateSelectProps {
    value: string;
    onChange: (value: string) => void;
}

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

export function DateSelect({ value, onChange }: DateSelectProps) {
    const [isOpen, setIsOpen] = React.useState(false);
    const selectRef = React.useRef<HTMLDivElement>(null);
    const dropdownRef = React.useRef<HTMLDivElement>(null);
    const [position, setPosition] = React.useState<Position>({
        top: 0,
        left: 0,
        direction: 'down'
    });

    // Initialize the view with the current local date or selected date
    const [viewDate, setViewDate] = React.useState(() => {
        if (value) {
            const [year, month] = value.split('-').map(Number);
            return { year, month: month - 1 };
        }
        const now = new Date();
        return {
            year: now.getFullYear(),
            month: now.getMonth()
        };
    });

    const calculatePosition = React.useCallback(() => {
        const inputElement = selectRef.current?.querySelector('input');
        if (!inputElement) return;

        const rect = inputElement.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const scrollY = window.scrollY || document.documentElement.scrollTop;

        const spaceBelow = viewportHeight - rect.bottom;

        const direction: Direction = spaceBelow >= DROPDOWN_HEIGHT ? 'down' : 'up';

        const newPosition: Position = {
            top: direction === 'down'
                ? rect.bottom + scrollY
                : rect.top + scrollY,
            left: rect.left + window.scrollX,
            direction
        };

        setPosition(newPosition);
    }, []);

    const handleToggle = (event: React.MouseEvent) => {
        event.preventDefault();
        event.stopPropagation();

        if (!isOpen) {
            calculatePosition();
        }
        setIsOpen(!isOpen);
    };

    React.useEffect(() => {
        if (!isOpen) return;

        const handleClickOutside = (event: MouseEvent) => {
            if (selectRef.current &&
                dropdownRef.current &&
                !selectRef.current.contains(event.target as Node) &&
                !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        const handleScroll = () => {
            calculatePosition();
        };

        document.addEventListener('mousedown', handleClickOutside);
        window.addEventListener('scroll', handleScroll, true);
        window.addEventListener('resize', calculatePosition);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            window.removeEventListener('scroll', handleScroll, true);
            window.removeEventListener('resize', calculatePosition);
        };
    }, [isOpen, calculatePosition]);

    // Calendar generation helpers
    const getDaysInMonth = (year: number, month: number) => {
        return new Date(year, month + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (year: number, month: number) => {
        return new Date(year, month, 1).getDay();
    };

    const formatDate = (date: Date): string => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    const handleDateSelect = (day: number) => {
        const selectedDate = new Date(viewDate.year, viewDate.month, day);
        onChange(formatDate(selectedDate));
        setIsOpen(false);
    };

    const handlePrevMonth = () => {
        setViewDate(prev => ({
            ...prev,
            month: prev.month === 0 ? 11 : prev.month - 1,
            year: prev.month === 0 ? prev.year - 1 : prev.year
        }));
    };

    const handleNextMonth = () => {
        setViewDate(prev => ({
            ...prev,
            month: prev.month === 11 ? 0 : prev.month + 1,
            year: prev.month === 11 ? prev.year + 1 : prev.year
        }));
    };

    const handlePrevYear = () => {
        setViewDate(prev => ({
            ...prev,
            year: prev.year - 1
        }));
    };

    const handleNextYear = () => {
        setViewDate(prev => ({
            ...prev,
            year: prev.year + 1
        }));
    };

    // Generate calendar days
    const calendarDays = React.useMemo(() => {
        const daysInMonth = getDaysInMonth(viewDate.year, viewDate.month);
        const firstDay = getFirstDayOfMonth(viewDate.year, viewDate.month);
        const days = [];

        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDay; i++) {
            days.push(null);
        }

        // Add the days of the month
        for (let i = 1; i <= daysInMonth; i++) {
            days.push(i);
        }

        return days;
    }, [viewDate.year, viewDate.month]);

    // Format display date in local timezone
    const displayDate = React.useMemo(() => {
        if (!value) return '';
        const [year, month, day] = value.split('-').map(Number);
        return new Date(year, month - 1, day).toLocaleDateString();
    }, [value]);

    return (
        <div ref={selectRef} className="relative w-full">
            <div className="relative">
                <Input
                    label="Date of Birth"
                    value={displayDate}
                    readOnly
                    color="blue"
                    className="cursor-pointer dark:text-white"
                    crossOrigin={undefined}
                    onClick={handleToggle}
                    placeholder="Select Date"
                    onPointerEnterCapture={() => {}}
                    onPointerLeaveCapture={() => {}}

                />
                <button
                    type="button"
                    onClick={handleToggle}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-100 rounded-full dark:hover:bg-gray-700"
                >
                    <Calendar className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                </button>
            </div>

            {isOpen && createPortal(
                <div
                    ref={dropdownRef}
                    className="fixed bg-white rounded-lg shadow-lg border border-gray-200 z-[9999] overflow-hidden dark:bg-gray-800 dark:border-gray-700"
                    style={{
                        position: 'fixed',
                        top: position.top,
                        left: position.left,
                        width: selectRef.current?.offsetWidth,
                        maxHeight: DROPDOWN_HEIGHT,
                        transform: position.direction === 'up'
                            ? `translateY(calc(-100% - ${SPACING}px))`
                            : `translateY(${SPACING}px)`
                    }}
                >
                    <div className="p-4">
                        {/* Month/Year Navigation */}
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={handlePrevYear}
                                    className="p-1 hover:bg-blue-50 rounded-md dark:hover:bg-gray-700"
                                >
                                    <ChevronsLeft className="h-4 w-4 dark:text-white" />
                                </button>
                                <button
                                    onClick={handlePrevMonth}
                                    className="p-1 hover:bg-blue-50 rounded-md dark:hover:bg-gray-700"
                                >
                                    <ChevronLeft className="h-4 w-4 dark:text-white" />
                                </button>
                            </div>

                            <span className="font-medium dark:text-white">
                                {MONTHS[viewDate.month]} {viewDate.year}
                            </span>

                            <div className="flex items-center gap-1">
                                <button
                                    onClick={handleNextMonth}
                                    className="p-1 hover:bg-blue-50 rounded-md dark:hover:bg-gray-700"
                                >
                                    <ChevronRight className="h-4 w-4 dark:text-white" />
                                </button>
                                <button
                                    onClick={handleNextYear}
                                    className="p-1 hover:bg-blue-50 rounded-md dark:hover:bg-gray-700"
                                >
                                    <ChevronsRight className="h-4 w-4 dark:text-white" />
                                </button>
                            </div>
                        </div>

                        {/* Days of Week Headers */}
                        <div className="grid grid-cols-7 gap-1 mb-2">
                            {DAYS_OF_WEEK.map(day => (
                                <div
                                    key={day}
                                    className="text-center text-sm font-medium text-gray-600 dark:text-gray-400"
                                >
                                    {day}
                                </div>
                            ))}
                        </div>

                        {/* Calendar Grid */}
                        <div className="grid grid-cols-7 gap-1">
                            {calendarDays.map((day, index) => {
                                const isSelected = value && day !== null && (
                                    value === formatDate(new Date(viewDate.year, viewDate.month, day))
                                );

                                return (
                                    <button
                                        key={index}
                                        type="button"
                                        className={`
                                            p-2 text-sm rounded-md flex items-center justify-center
                                            ${!day ? 'invisible' : 'hover:bg-blue-50 dark:hover:bg-gray-700'}
                                            ${isSelected
                                                ? 'bg-blue-500 text-white hover:bg-blue-600'
                                                : 'dark:text-white'}
                                        `}
                                        onClick={() => day && handleDateSelect(day)}
                                        disabled={!day}
                                    >
                                        {day}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </div>
    );
}