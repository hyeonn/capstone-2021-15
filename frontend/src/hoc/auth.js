import React, { useEffect } from 'react';
import axios from 'axios';

export default function (SpecificComponent, option, adminRoute = null) {
    // option: null, true, false
    // null: 아무나 출입 가능 -> 회원가입 페이지, 로그인 페이지
    // true: 로그인한 유저만 출입 가능 => auth 페이지, 메인페이지
    // false: 로그인한 유저는 출입 불가능 -> 회원가입 페이지. 로그인 페이지

    // adminRoute: 관리자만 출입 가능 페이지. 기본적으로 다 null
    function AuthenticationCheck(props) {
        useEffect(() => {
            axios.get('/api/user/auth').then(response => {
                if( !response.data.isAuth) {
                    if( option) {
                        props.history.push('/login');
                    }
                } else{
                    // 로그인한 상태
                    if(adminRoute && !response.payload.isAuth) { // 로그인은 헀지만 관리자는 아님
                        props.history.push('/'); 
                    } else { // 로그인 했는데 회원가입, 로그인 페이지로 접근하려고 할 때
                        props.history.push('/');
                    }
                }
            })

        }, [])

        return (
            <SpecificComponent />
        )
    }

    return AuthenticationCheck
}
